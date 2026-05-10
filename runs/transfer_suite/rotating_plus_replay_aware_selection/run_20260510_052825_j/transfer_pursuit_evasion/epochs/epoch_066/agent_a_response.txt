def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    self_role = observation.get("self_role", "pursuer")

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    # Deterministic move ordering: favor x then y, diagonals, and staying still as fallback.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            moves.append((dx, dy))
    moves += [(0, 0)]

    curd = dist2(sx, sy)
    best = None
    best_val = None

    # For pursuer: minimize distance; for evader: maximize distance.
    # Also add mild penalty for moving closer/farther relative to direct direction to reduce dithering.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = dist2(nx, ny)
        if self_role == "evader":
            val = nd
        else:
            val = -nd

        # Wall-hugging / stability: discourage no-op into obstacles-free but unhelpful moves.
        if val == (best_val if best_val is not None else val):
            pass

        if best is None:
            best = (dx, dy)
            best_val = val
        else:
            if self_role == "evader":
                if val > best_val:
                    best, best_val = (dx, dy), val
            else:
                if val > best_val:
                    best, best_val = (dx, dy), val

    if best is not None:
        return [int(best[0]), int(best[1])]

    # If all moves invalid (should be rare), stay put deterministically.
    return [0, 0]