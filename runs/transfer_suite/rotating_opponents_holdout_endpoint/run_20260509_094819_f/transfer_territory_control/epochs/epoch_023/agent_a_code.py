def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    def to_set(v):
        if not v:
            return set()
        if isinstance(v, dict):
            it = v.keys()
        else:
            it = v
        out = set()
        for p in it:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                out.add((int(p[0]), int(p[1])))
        return out
    obstacles = to_set(observation.get("obstacles") or [])
    resources = to_set(observation.get("resources") or [])
    unclaimed = to_set(observation.get("unclaimed_cells") or [])
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d): return abs(a - c) + abs(b - d)
    targets = list(resources) if resources else list(unclaimed)
    if not targets:
        return [0, 0]
    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = int(sx) + dx, int(sy) + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = min(man(nx, ny, tx, ty) for (tx, ty) in targets)
            score = d + (0 if (nx, ny) in resources else 3) + (0 if (nx, ny) != (ox, oy) else -2)
            if best is None or score < best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
    return [0, 0] if best is None else [int(best[1][0]), int(best[1][1])]