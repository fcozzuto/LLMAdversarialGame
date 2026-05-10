def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = [tuple(map(int, c[:2])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if unclaimed:
            d = min(man((nx, ny), c) for c in unclaimed)
            # Prefer closer to unclaimed; also slightly avoid moving toward opponent.
            val = (-d, man((nx, ny), (ox, oy)))
        else:
            # Fallback: drift toward center while avoiding opponent.
            cx, cy = (W - 1) // 2, (H - 1) // 2
            val = (-man((nx, ny), (cx, cy)), man((nx, ny), (ox, oy)))
        key = (val[0], -val[1], dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    if best is not None:
        return best[1]
    return [0, 0]