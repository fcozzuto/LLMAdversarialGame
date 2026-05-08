def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = lambda x, y: inb(x, y) and (x, y) not in obs

    # Precompute BFS distances from any cell to target (opponent) via 8-neighborhood and obstacles
    def bfs(startx, starty, tx, ty):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not legal(tx, ty) or not legal(startx, starty):
            return max(abs(startx - tx), abs(starty - ty))
        q = [(tx, ty)]
        qi = 0
        dist[tx][ty] = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            d = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if legal(nx, ny) and d < dist[nx][ny]:
                    dist[nx][ny] = d
                    q.append((nx, ny))
        return dist[startx][starty]

    # One-step minimax on resulting capture-distance (0 means capture)
    best = None
    best_val = 10**9
    # Deterministic tie-break order: prefer moves with smaller dx,dy lexicographically
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            candidates.append((dx, dy))
    candidates.sort(key=lambda t: (t[0] + t[1]*0, t[0], t[1]))

    for dx, dy in candidates if candidates else [(0, 0)]:
        ax, ay = sx + dx, sy + dy
        # Opponent chooses move maximizing our shortest-path distance to their new position
        worst = -1
        # Opponent may also be forced by obstacles; assume they can choose among legal cells
        for odx, ody in moves:
            bx, by = ox + odx, oy + ody
            if not legal(bx, by):
                continue
            d_to = bfs(ax, ay, bx, by)
            if d_to > worst:
                worst = d_to
            # If capture is certain for this our move, we can break early
            if worst == 0:
                break
        # If opponent has no legal moves (fully blocked), evaluate against staying
        if worst < 0:
            worst = bfs(ax, ay, ox, oy)

        # Prefer smaller worst-case distance; tie-break by lexicographic move order
        if worst < best_val:
            best_val = worst
            best = [dx, dy]

    if best is None:
        best = [0, 0]
    return [int(best[0]), int(best[1])]