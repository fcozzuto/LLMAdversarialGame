def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_move_towards(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            return [0, 0]
        return [dx, dy]

    def dist2(x, y, tx, ty):
        dx = x - tx
        dy = y - ty
        return dx * dx + dy * dy

    # Candidate targets: nearest resources; deterministic tie-break by coordinates
    targets = sorted(resources, key=lambda p: (dist2(sx, sy, p[0], p[1]), p[0], p[1]))

    # Prefer resources that are also not "immediately occupied" by opponent move (avoid stepping onto opponent)
    opp = (ox, oy)
    for p in targets:
        tx, ty = p
        move = best_move_towards(tx, ty)
        nx, ny = sx + move[0], sy + move[1]
        if (nx, ny) != opp:
            return move

    # If stepping onto opponent is unavoidable, take the best resource anyway
    for p in targets:
        return best_move_towards(p[0], p[1])

    # No resources visible: move to center-ish deterministically while avoiding obstacles and opponent
    cx, cy = w // 2, h // 2
    dx = 0 if cx == sx else (1 if cx > sx else -1)
    dy = 0 if cy == sy else (1 if cy > sy else -1)
    nx, ny = sx + dx, sy + dy
    if not inside(nx, ny) or (nx, ny) in obstacles or (nx, ny) == opp:
        # Try simple ordered alternatives
        for adx in (0, -1, 1):
            for ady in (0, -1, 1):
                if adx == 0 and ady == 0:
                    continue
                if abs(adx) > 1 or abs(ady) > 1:
                    continue
                px, py = sx + adx, sy + ady
                if inside(px, py) and (px, py) not in obstacles and (px, py) != opp:
                    return [adx, ady]
        return [0, 0]

    return [dx, dy]