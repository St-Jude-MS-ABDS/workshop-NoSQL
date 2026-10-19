// =============================================================================
//  MongoDB first-start script  (runs ONCE, when the data volume is empty)
// =============================================================================
//  Goal: reproduce the "classroom" permission model on your laptop, so that you can
//  learn RBAC (Role-Based Access Control) hands-on.
//
//     user      databases it can reach                        roles
//     --------  -------------------------------------------   -------------------------------
//     admin     everything                                    root            (created by Docker)
//     student   public      -> shared teaching data           read            (look, don't touch)
//               student_db  -> your personal sandbox          readWrite + dbAdmin
//
//  The Docker image has already created `admin` and switched authentication on.
//  Here we only add the restricted `student` account.
//
//  This file is executed by `mongosh`; the `db` variable is the default database.
//  If you want to re-run it, wipe the data volume first:   docker compose down -v

const admin = db.getSiblingDB("admin");

// createUser(): the roles array is the heart of RBAC.
//   * { role: "read",      db: "public" }      -> find / count / aggregate ... but no writes
//   * { role: "readWrite", db: "student_db" }  -> full CRUD on documents
//   * { role: "dbAdmin",   db: "student_db" }  -> create indexes, view stats, drop collections
admin.createUser({
  user: "student",
  pwd: "student_password",
  roles: [
    { role: "read", db: "public" },
    { role: "readWrite", db: "student_db" },
    { role: "dbAdmin", db: "student_db" },
  ],
});

print("[init] created user 'student' with read@public + readWrite/dbAdmin@student_db");
