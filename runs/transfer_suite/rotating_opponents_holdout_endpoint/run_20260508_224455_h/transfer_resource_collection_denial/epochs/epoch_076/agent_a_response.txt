def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    gw, gh = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    res = [(int(r[0]), int(r[1])) for r in resources]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_score = -10**18

    # Deterministic ordering among equal scores
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # If we step on a resource, heavily prefer it
        if (nx, ny) in obstacles:
            continue
        step_collect_bonus = 0
        if (nx, ny) in set(res):
            step_collect_bonus = 10**9

        my_best_lead = -10**18
        my_best_myd = 10**18
        worst_op_dist = -10**18  # prefer reducing opponent options

        for rx, ry in res:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            lead = od - md  # positive means we're closer than opponent to this resource
            if lead > my_best_lead or (lead == my_best_lead and md < my_best_myd):
                my_best_lead = lead
                my_best_myd = md
            # For denial, track best (closest) opponent distance to any resource that we would not "cover"
            if od > worst_op_dist:
                worst_op_dist = od

        # Denier archetype: race the opponent by maximizing lead and minimizing our own distance.
        # Also slightly penalize states where opponent has many nearby resources (approximated by maximizing opponent distance to nearest?).
        # Since we can't know coverage set, use average of closest opponent distance proxy via minimum over resources.
        min_opd = 10**18
        for rx, ry in res:
            od = cheb(ox, oy, rx, ry)
            if od < min_opd:
                min_opd = od
        # Convert to a "pressure": smaller min_opd means opponent already close to something (hard mode) -> prefer stronger lead.
        pressure = -min_opd

        score = step_collect_bonus + (my_best_lead * 10**6) - (my_best_myd * 10**3) + (pressure * 10)
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]