def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs = set(tuple(p) for p in observation.get("obstacles", []))
    res = [tuple(p) for p in observation.get("resources", [])]
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_dir(targets):
        if not targets:
            return (0, 0)
        best = None
        bestd = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = min(max(abs(nx - tx), abs(ny - ty)) for tx, ty in targets)
            if bestd is None or d < bestd:
                bestd = d
                best = (dx, dy)
        return best if best is not None else (0, 0)

    if res:
        return list(best_dir(res))
    return list(best_dir([(ox, oy)]))