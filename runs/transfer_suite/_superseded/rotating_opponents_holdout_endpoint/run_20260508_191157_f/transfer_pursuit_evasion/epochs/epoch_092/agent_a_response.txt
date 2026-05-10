def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_role = observation.get("self_role", "pursuer")
    cap = int(observation.get("capture_radius", 0))

    def bfs_dist(start, goal):
        if start == goal:
            return 0
        q = [start]
        dist = {start: 0}
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            d = dist[(x, y)] + 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if nx < 0 or nx >= w or ny < 0 or ny >= h:
                        continue
                    if (nx, ny) in obstacles:
                        continue
                    if (nx, ny) not in dist:
                        dist[(nx, ny)] = d
                        if (nx, ny) == goal:
                            return d
                        q.append((nx, ny))
        return 10**9

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_val = None

    if self_role == "pursuer":
        # Try to move onto opponent (or get closer along shortest paths).
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            if cap == 0 and (nx, ny) == (ox, oy):
                return [dx, dy]
            d = bfs_dist((nx, ny), (ox, oy))
            val = -d
            if best is None or val > best_val or (val == best_val and (dx, dy) < best):
                best, best_val = (dx, dy), val
    else:
        # Evade: maximize shortest-path distance from opponent.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            d = bfs_dist((nx, ny), (ox, oy))
            # Keep options open: prefer not to step onto same-cell candidates at minimal distance.
            val = d + 0.001 * (abs(nx - 0) + abs(ny - 0))  # deterministic tie-break
            if best is None or val > best_val or (val == best_val and (dx, dy) < best):
                best, best_val = (dx, dy), val

        # If all blocked (shouldn't happen), stay.
        if best is None:
            best = (0, 0)

    return [int(best[0]), int(best[1])]