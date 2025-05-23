from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Node(Base):
    __tablename__ = 'nodes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    graph_id = Column(Integer, ForeignKey('graphs.id'))

    __table_args__ = (
        UniqueConstraint('name', 'graph_id'),
    )

    edges_in = relationship(
        "Edge", foreign_keys="Edge.target_id", back_populates="target_node", cascade="all, delete-orphan")
    edges_out = relationship(
        "Edge", foreign_keys="Edge.source_id", back_populates="source_node", cascade="all, delete-orphan")

    graph = relationship("Graph", back_populates="nodes")


class Edge(Base):
    __tablename__ = 'edges'
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey('nodes.id'))
    target_id = Column(Integer, ForeignKey('nodes.id'))

    graph_id = Column(Integer, ForeignKey('graphs.id'))

    source_node = relationship("Node", foreign_keys=[
                               source_id], back_populates="edges_out")
    target_node = relationship("Node", foreign_keys=[
                               target_id], back_populates="edges_in")
    
    __table_args__ = (
        UniqueConstraint('graph_id', 'source_id', 'target_id'),
    )

    graph = relationship("Graph", back_populates="edges")


class Graph(Base):
    __tablename__ = 'graphs'
    id = Column(Integer, primary_key=True, index=True)

    nodes = relationship("Node", back_populates="graph",
                         cascade="all, delete-orphan")
    edges = relationship("Edge", back_populates="graph",
                         cascade="all, delete-orphan")
