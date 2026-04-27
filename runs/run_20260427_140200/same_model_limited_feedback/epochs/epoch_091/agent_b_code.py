def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])

    def clamp(x, a, b):
        return a if x < a else b if x > b else x

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # Pick best target resource by arrival advantage
    best_t = None
    best_score = None
    for rx, ry in resources:
        ds = dist2(sx, sy, rx, ry)
        do = dist2(ox, oy, rx, ry)
        score = (do - ds) - 0.001 * (rx + 31 * ry)  # deterministic tie-break
        if best_score is None or score > best_score:
            best_score = score
            best_t = (rx, ry)

    # If no resources known, head toward opponent or center deterministically
    if best_t is None:
        tx, ty = (w // 2, h // 2)
        if dist2(sx, sy, tx, ty) < dist2(sx, sy, ox, oy):
            best_t = (tx, ty)
        else:
            best_t = (ox, oy)

    tx, ty = best_t
    moves = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx = clamp(sx + dx, 0, w - 1)
            ny = clamp(sy + dy, 0, h - 1)
            moves.append((dx, dy, nx, ny))

    # Evaluate candidate moves
    best_move = (0, 0)
    best_val = None
    for dx, dy, nx, ny in moves:
        if (nx, ny) in obstacles:
            continue
        self_d = dist2(nx, ny, tx, ty)
        opp_d = dist2(nx, ny, ox, oy)
        # discourage moving onto opponent and favor earlier capture
        val = self_d - 0.12 * opp_d
        # slight preference for staying within grid and moving if equal
        val += 0.0001 * (abs(dx) + abs(dy))
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]