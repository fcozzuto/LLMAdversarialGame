def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_role = str(observation.get("self_role", "")).lower()
    my_is_pursuer = ("pursur" in self_role) or (self_role == "pursuer")
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    start = (sx, sy)
    target = (ox, oy)

    def bfs_from_goal(goal):
        gx, gy = goal
        if not valid(gx, gy):
            return None
        INF = 10**9
        dist = [[INF] * w for _ in range(h)]
        dist[gy][gx] = 0
        q = [(gx, gy)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            d0 = dist[y][x] + 1
            for dx, dy in cand:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and d0 < dist[ny][nx]:
                    dist[ny][nx] = d0
                    q.append((nx, ny))
        return dist

    dist_to_opp = bfs_from_goal(target)
    if dist_to_opp is None:
        dx = 0 if sx == 0 else -1
        dy = 0 if sy == 0 else -1
        return [dx, dy]

    def best_step(for_pursuer):
        best = None
        bestv = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                nx, ny = sx, sy
                dx, dy = 0, 0
            d = dist_to_opp[ny][nx]
            if d >= 10**9:
                d = 10**9 - 1
            # Pursuer minimizes distance; evader maximizes.
            # Tie-break deterministically toward/away from opponent.
            toward = abs(nx - ox) + abs(ny - oy)
            v = (-d, toward) if for_pursuer else (d, -toward)
            if best is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return best

    dx, dy = best_step(my_is_pursuer)
    return [int(dx), int(dy)]