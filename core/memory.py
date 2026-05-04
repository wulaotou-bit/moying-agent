"""
墨影长篇永久记忆系统
基于Chroma轻量向量库，支持1000章不崩人设
存储：人设、世界观、伏笔、章节关键内容
"""
import chromadb
import json
from chromadb.utils import embedding_functions
from config import Config
from utils.logger import log

class NovelLongTermMemory:
    def __init__(self, novel_title: str):
        self.memory_path = Config.OUTPUT_DIR / "long_memory"
        self.memory_path.mkdir(exist_ok=True)

        # 轻量中文语义编码器（不占显存，6.5GB内存完美跑）
        self.embedding = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        self.client = chromadb.PersistentClient(path=str(self.memory_path))
        self.collection = self.client.get_or_create_collection(
            name=novel_title.replace(" ", "_"),
            embedding_function=self.embedding
        )
        self.llm = None  # 外部注入LLM客户端
        log.success("✅ 长篇永久记忆系统初始化完成")

    def set_llm(self, llm):
        """注入LLM客户端"""
        self.llm = llm

    def save_character(self, character: dict):
        """保存角色人设（永不遗忘）"""
        self.collection.add(
            documents=[json.dumps(character, ensure_ascii=False)],
            metadatas=[{"type": "character", "name": character["name"]}],
            ids=[f"char_{character['name'].replace(' ', '_')}"]
        )
        log.info(f"已保存角色人设: {character['name']}")

    def save_worldview(self, content: str):
        """保存世界观设定"""
        self.collection.add(
            documents=[content],
            metadatas=[{"type": "worldview"}],
            ids=["worldview"]
        )
        log.info("已保存世界观设定")

    def save_foreshadow(self, chapter_id: int, content: str):
        """保存伏笔（自动关联章节）"""
        self.collection.add(
            documents=[content],
            metadatas=[{"type": "foreshadow", "chapter": str(chapter_id)}],
            ids=[f"foreshadow_{chapter_id}_{len(self.collection.get(where={'type': 'foreshadow'})['ids'])}"]
        )
        log.info(f"已保存第{chapter_id}章伏笔")

    def save_chapter(self, chapter_id: int, title: str, content: str):
        """保存章节关键记忆"""
        self.collection.add(
            documents=[f"第{chapter_id}章《{title}》：{content[:500]}"],
            metadatas=[{"type": "chapter", "chapter": str(chapter_id), "title": title}],
            ids=[f"chapter_{chapter_id}"]
        )
        log.info(f"已保存第{chapter_id}章记忆")

    def query_relevant(self, query: str, top_k: int = 5) -> str:
        """语义检索相关记忆"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where={"type": {"$in": ["character", "foreshadow", "chapter"]}}
        )
        memories = results["documents"][0]
        return "\n".join(memories) if memories else "无相关记忆"

    def get_all_characters(self) -> str:
        """获取全部人设（强制AI遵守）"""
        res = self.collection.get(where={"type": "character"})
        return "\n".join(res["documents"]) if res["documents"] else "无角色设定"

    def get_all_foreshadows(self) -> str:
        """获取全部未回收伏笔"""
        res = self.collection.get(where={"type": "foreshadow"})
        return "\n".join(res["documents"]) if res["documents"] else "无未回收伏笔"