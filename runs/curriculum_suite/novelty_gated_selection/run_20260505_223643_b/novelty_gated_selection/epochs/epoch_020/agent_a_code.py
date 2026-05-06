def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []

    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort(key=lambda t: (t[0], t[1]))

    best_res = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        our_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        # Prefer resources where we are relatively closer; tie-break by absolute closeness.
        key = (-(opp_d - our_d), our_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res
    best_move = (0, 0)
    best_score = None

    # Small intercept behavior: if opponent is closer to the target, bias toward denying by moving closer to opponent.
    opp_closer = man(ox, oy, tx, ty) < man(sx, sy, tx, ty)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        our_next = man(nx, ny, tx, ty)
        # Also consider moving away from opponent slightly if opponent is close to the target.
        opp_next_to_opp = man(nx, ny, ox, oy)
        opp_next_to_target = man(ox, oy, tx, ty)

        score = (our_next,
                 0 if not opp_closer else opp_next_to_opp,
                 opp_next_to_target,
                 abs(dx) + abs(dy),
                 dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]