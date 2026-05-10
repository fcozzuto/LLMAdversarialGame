def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for c in observation.get("unclaimed_cells") or []:
        if c and len(c) >= 2:
            unclaimed.add((int(c[0]), int(c[1])))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    targets = list(unclaimed) if unclaimed else [(ox, oy)]
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        mind = 10**9
        for t in targets:
            if inb(t[0], t[1]):
                d = dist((nx, ny), t)
                if d < mind:
                    mind = d

        s = -mind * 10 + dist((nx, ny), (ox, oy))
        if best_score is None or s > best_score:
            best_score = s
            best = [dx, dy]

    return best if best is not None else [0, 0]