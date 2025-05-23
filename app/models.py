from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
 
Base = declarative_base()
 
class Vertex(Base):
    __tablename__ = 'vertices'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), index=True)
    graph_id = Column(Integer, ForeignKey('graphs.id'))
    __table_args__ = (UniqueConstraint('name', 'graph_id'),)
 
    incoming_edges = relationship(
        "Edge",
        foreign_keys="Edge.target_id",
        back_populates="target_vertex",
        cascade="all, delete-orphan"
    )
    outgoing_edges = relationship(
        "Edge",
        foreign_keys="Edge.source_id",
        back_populates="source_vertex",
        cascade="all, delete-orphan"
    )
    graph = relationship("Graph", back_populates="vertices")
 
class Edge(Base):
    __tablename__ = 'edges'
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('vertices.id'))
    target_id = Column(Integer, ForeignKey('vertices.id'))
    graph_id = Column(Integer, ForeignKey('graphs.id'))
 
    source_vertex = relationship("Vertex", foreign_keys=[source_id], back_populates="outgoing_edges")
    target_vertex = relationship("Vertex", foreign_keys=[target_id], back_populates="incoming_edges")
    graph = relationship("Graph", back_populates="edges")
    __table_args__ = (UniqueConstraint('graph_id', 'source_id', 'target_id'),)
 
class Graph(Base):
    __tablename__ = 'graphs'
    id = Column(Integer, primary_key=True)
    vertices = relationship("Vertex", back_populates="graph", cascade="all, delete-orphan")
    edges = relationship("Edge", back_populates="graph", cascade="all, delete-orphan")
