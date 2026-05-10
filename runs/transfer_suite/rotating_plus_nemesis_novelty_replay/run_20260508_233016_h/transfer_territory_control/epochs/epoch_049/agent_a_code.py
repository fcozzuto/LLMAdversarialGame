def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w, h = observation.get("grid_width", 1), observation.get("grid_height", 1)
    ox, oy = observation.get("opponent_position", (sx, sy))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    tx_list = observation.get("unclaimed_cells")
    if not tx_list:
        tx_list = observation.get("resources") or []
    if not tx_list:
        tx_list = [(w // 2, h // 2)]
    targets = [tuple(p) for p in tx_list]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dt = 10**9
        for tx, ty in targets[:50]:
            d = man(nx, ny, tx, ty)
            if d < dt:
                dt = d
        do = man(nx, ny, ox, oy)
        score = -dt * 1000 + do  # go toward target, stay away from opponent on ties
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]