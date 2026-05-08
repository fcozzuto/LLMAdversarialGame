def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                x, y = int(x), int(y)
                if 0 <= x < w and 0 <= y < h:
                    obstacles.add((x, y))
    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                if (x, y) not in obstacles:
                    unclaimed.add((x, y))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1), (0, 0)]
    best = None
    bestv = -10**9
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def score(x, y):
        v = 0
        if (x, y) in unclaimed:
            v += 12
            if x == 0 or y == 0 or x == w - 1 or y == h - 1:
                v += 6
        # Encourage moves that are near opponent
        if max(abs(x - ox), abs(y - oy)) == 1:
            v += 8
        # Prefer staying away from obstacles indirectly
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    v -= 3
        # Slightly prefer moving toward center if nothing else
        v -= 0.2 * (abs(x - cx) + abs(y - cy))
        return v

    for dx, dy in moves:
        x, y = sx + dx, sy + dy
        if not (0 <= x < w and 0 <= y < h):
            continue
        if (x, y) in obstacles:
            continue
        v = score(x, y)
        if v > bestv:
            bestv = v
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best