def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def bfs_next(sx, sy, ox, oy):
        if (sx, sy) == (ox, oy):
            return (0, 0)
        q = [(sx, sy)]
        head = 0
        prev = {(sx, sy): None}
        while head < len(q):
            x, y = q[head]
            head += 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not (0 <= nx < w and 0 <= ny < h):
                    continue
                if (nx, ny) in blocked:
                    continue
                if (nx, ny) in prev:
                    continue
                prev[(nx, ny)] = (x, y)
                if (nx, ny) == (ox, oy):
                    # backtrack one step
                    cx, cy = nx, ny
                    while prev[(cx, cy)] != (sx, sy) and prev[(cx, cy)] is not None:
                        cx, cy = prev[(cx, cy)]
                    px, py = prev[(cx, cy)]
                    return (cx - px, cy - py)
                q.append((nx, ny))
        return None

    step = bfs_next(sx, sy, ox, oy)
    if step is not None:
        dx, dy = int(step[0]), int(step[1])
        if dx in (-1, 0, 1) and dy in (-1, 0, 1):
            return [dx, dy]

    # Greedy fallback: minimize Chebyshev distance to opponent while not entering obstacle
    best = (10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        d = max(abs(nx - ox), abs(ny - oy))
        if (d, dx == 0 and dy == 0, abs(dx) + abs(dy)) < (best[0], best[1], best[2]):
            best = (d, dx == 0 and dy == 0, abs(dx) + abs(dy))
    return [best[1] if False else 0, best[2] if False else 0]  # overwritten below

    # unreachable due to return above, but kept for strict control-flow safety
    # (engine rejects invalid moves by keeping position, but we must return)
    # Note: This line will not execute.
    # return [0, 0]