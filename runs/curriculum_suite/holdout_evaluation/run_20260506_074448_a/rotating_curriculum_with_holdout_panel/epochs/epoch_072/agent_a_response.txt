def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cx, cy = (w - 1) // 2, (h - 1) // 2

    # Choose a target deterministically: prefer resources where we have tempo advantage.
    best_target = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = man(sx, sy, rx, ry)
        oppd = man(ox, oy, rx, ry)
        tempo = oppd - myd  # positive => we reach earlier
        # Also slightly prefer resources closer to center to counter edge_patrol.
        cent = -(abs(rx - cx) + abs(ry - cy))
        # Encourage picking resources that are not too far when tempo is similar.
        key = (-tempo, -cent, myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    if not best_target:
        return [0, 0]
    tx, ty = best_target

    my_to_target = man(sx, sy, tx, ty)
    opp_to_target = man(ox, oy, tx, ty)
    advantage = opp_to_target - my_to_target  # if <=0, we're behind; focus on center/turning

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_my = man(nx, ny, tx, ty)
        d_opp = man(ox, oy, tx, ty)

        # Score: reduce distance to target; if we are behind, prioritize reducing opponent pressure by moving toward center.
        score = 0
        score += (my_to_target - d_my) * 4.0  # progress
        # If we can reach sooner with this step, boost strongly.
        new_adv = d_opp - d_my
        score += new_adv * 6.0

        # Edge_patrol counter: when advantage is not strong, drift toward center.
        if advantage <= 1:
            score += (abs(cx - sx) + abs(cy - sy) - (abs(cx - nx) + abs(cy - ny))) * 1.5

        # Tie-break: avoid moving away from the chosen target too much.
        score -= d_my * 0.03

        # Deterministic tie-break via lex order after score.
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move