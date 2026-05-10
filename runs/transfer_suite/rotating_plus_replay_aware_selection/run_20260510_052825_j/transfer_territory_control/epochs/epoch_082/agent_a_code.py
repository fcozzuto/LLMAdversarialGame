def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation.get("opponent_position", (None, None))
    obstacles = observation.get("obstacles") or []
    obst = {tuple(p) for p in obstacles if p and len(p) == 2}
    unclaimed = observation.get("unclaimed_cells") or []
    unclaim = {tuple(p) for p in unclaimed if p and len(p) == 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    best = None
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        sc = 0
        if (nx, ny) in unclaim:
            sc += 1000
        if ox is not None and oy is not None:
            sc += 2 * (abs(nx - ox) + abs(ny - oy))  # stay farther from opponent
        sc -= (abs(nx - sx) + abs(ny - sy))  # slight preference to be closer to current
        if sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    if best is not None:
        return [best[0], best[1]]
    return [0, 0]