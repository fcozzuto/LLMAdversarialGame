def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    is_pursuer = any(k in sr for k in ("pursuer", "hunter", "chaser"))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs_from(start):
        if not inb(start[0], start[1]):
            return None
        dist = {(start[0], start[1]): 0}
        q = [(start[0], start[1])]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[(x, y)] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in dist:
                    dist[(nx, ny)] = nd
                    q.append((nx, ny))
        return dist

    # Compute shortest-path distances to opponent (used for pursuer/evader scoring)
    dist_to_op = bfs_from((ox, oy)) or {}
    # Candidates from legal one-step moves
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            d = dist_to_op.get((nx, ny), 10**9)
            legal.append((dx, dy, d, max(abs(nx - ox), abs(ny - oy))))
    if not legal:
        return [0, 0]

    # Deterministic tie-break: (primary objective, then euclid-ish, then dx/dy)
    if is_pursuer:
        # minimize shortest path distance; tie-break by smaller chebyshev and then lexicographic move
        legal.sort(key=lambda t: (t[2], t[3], t[0], t[1]))
        return [legal[0][0], legal[0][1]]
    else:
        # maximize distance from opponent: prefer larger shortest-path distance; if unreachable, keep low penalty via chebyshev
        legal.sort(key=lambda t: (-t[2], -t[3], t[0], t[1]))
        return [legal[0][0], legal[0][1]]