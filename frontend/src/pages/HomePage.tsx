import React from "react";
import { useLoaderData } from "react-router";


interface Post {
  id: string;
  title: string;
  // add additional fields returned by loader as needed
}


const HomePage:React.FC = () =>  {
  const { posts } = useLoaderData<{ posts: Post[] }>();
  return (
    <div>
      <h1>Home Page1</h1>
      {posts.map(p => (
        <div key={p.id}>{p.title}</div>
      ))}
    </div>
  );
}

export default HomePage

