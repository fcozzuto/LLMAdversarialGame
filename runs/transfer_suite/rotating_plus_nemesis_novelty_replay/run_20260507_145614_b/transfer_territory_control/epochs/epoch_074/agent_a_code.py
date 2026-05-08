def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        # Prefer closer to opponent, then larger movement component (avoid zigzag), then lexicographic
        key = (dist, -(abs(dx) + abs(dy)), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is not None:
        return best

    # Fallback: try any in-bounds non-obstacle move, else stay
    for dx, dy in moves + [(0, 0)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [dx, dy]
    return [0, 0]