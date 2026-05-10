def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    sp = observation.get("self_path") or []
    last = tuple(sp[-1]) if sp else None

    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h
    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    best = None
    bestv = -10**9
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) == last:
            revisit_pen = -5
        else:
            revisit_pen = 0

        if (nx, ny) in unclaimed:
            v = 100 - dist(nx, ny, ox, oy)
        elif (nx, ny) in oppT:
            v = 60 - dist(nx, ny, ox, oy)
        elif (nx, ny) in selfT:
            v = 10 - dist(nx, ny, ox, oy) // 2
        else:
            v = -dist(nx, ny, ox, oy)

        v += revisit_pen
        if v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best