import { useEffect, useState } from 'react';
import axios from 'axios';
import Link from 'next/link';

interface Semester {
  acy: number;
  sem: number;
}

interface Course {
  id: number;
  acy: number;
  sem: number;
  crs_no: string;
  name: string;
  teacher?: string;
}

export default function Home() {
  const [semesters, setSemesters] = useState<Semester[]>([]);
  const [selected, setSelected] = useState<Semester | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);

  useEffect(() => {
    // Fetch available semesters from the API
    axios.get('/api/semesters')
      .then((res) => setSemesters(res.data))
      .catch((err) => console.error(err));
  }, []);

  useEffect(() => {
    if (selected) {
      axios.get('/api/courses', { params: { acy: selected.acy, sem: selected.sem } })
        .then((res) => setCourses(res.data))
        .catch((err) => console.error(err));
    }
  }, [selected]);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">NYCU Course Explorer</h1>
      <div className="mb-4">
        <select
          className="p-2 border rounded"
          onChange={(e) => {
            const value = e.target.value;
            if (!value) {
              setSelected(null);
              setCourses([]);
            } else {
              const [acyStr, semStr] = value.split('-');
              setSelected({ acy: parseInt(acyStr, 10), sem: parseInt(semStr, 10) });
            }
          }}
        >
          <option value="">Choose a semester…</option>
          {semesters.map((s) => (
            <option key={`${s.acy}-${s.sem}`} value={`${s.acy}-${s.sem}`}>
              {s.acy} {s.sem === 1 ? 'Fall' : 'Spring'}
            </option>
          ))}
        </select>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {courses.map((course) => (
          <div key={course.id} className="border rounded p-4 shadow hover:shadow-lg transition">
            <Link href={`/course/${course.id}`}>
              <a>
                <h2 className="font-semibold text-lg mb-1">{course.name}</h2>
                <p className="text-sm text-gray-600">{course.crs_no} {course.teacher ? `· ${course.teacher}` : ''}</p>
              </a>
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}