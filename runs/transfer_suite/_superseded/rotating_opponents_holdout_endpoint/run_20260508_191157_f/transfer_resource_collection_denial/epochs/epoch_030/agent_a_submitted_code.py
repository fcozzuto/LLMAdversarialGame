def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((x, y) for x, y in (observation.get("obstacles") or []))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    if not resources:
        return [0, 0]

    # Pick a target resource where we can create/maintain the biggest lead.
    # Lead score uses (opp_dist - my_dist) primarily; also breaks ties by preferring closeness.
    target = None
    target_lead = -10**18
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        lead = (opd - myd) * 1000 - myd
        # discourage going to a resource that is adjacent to opponent but not ours
        if man(ox, oy, rx, ry) <= 1 and man(sx, sy, rx, ry) > 1:
            lead -= 500
        if lead > target_lead:
            target_lead = lead
            target = (rx, ry)

    tx, ty = target

    # Evaluate local moves toward the chosen target, but penalize moves that let the opponent get closer too.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        myd_next = man(nx, ny, tx, ty)
        myd_now = man(sx, sy, tx, ty)

        # Distance shaping
        score = (myd_now - myd_next) * 120

        # Maintain lead against opponent for the same target
        opd_now = man(ox, oy, tx, ty)
        opd_next = man(ox, oy, tx, ty)  # opponent hasn't moved yet; steady comparison
        lead_now = opd_now - myd_now
        lead_next = opd_next - myd_next
        score += (lead_next - lead_now) * 300

        # If target is already reached, stay; else avoid getting too close to opponent unless it helps collect
        if (sx, sy) == (tx, ty):
            score += 1000
        else:
            if man(nx, ny, ox, oy) <= 1:
                score -= 250

        # Mild obstacle awareness: penalize moves that step away from any available resource directionless
        # (deterministic and cheap): prefer reducing distance to closest resource overall.
        closest_now = min(manh(sx, sy, r[0], r[1]) for r in resources)
        closest_next = min(manh(nx, ny, r[0], r[1]) for r in resources)
        score += (closest_now - closest_next) * 10

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]