def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    # Focus on closest resources to reduce brittleness
    dlist = sorted(((man(sx, sy, rx, ry), rx, ry) for rx, ry in resources), key=lambda t: t[0])
    top = [(rx, ry) for _, rx, ry in dlist[:10]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy

        # If we step onto a resource, prioritize strongly
        capture_bonus = 0
        if (nx, ny) in set(resources):
            capture_bonus = 1000 - man(nx, ny, ox, oy)

        # Evaluate best target based on our progress vs opponent
        # Prefer targets where opponent is farther and where we reduce our distance.
        my_best = 10**9
        opp_best = 10**9
        for rx, ry in top:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            if sd < my_best:
                my_best = sd
            if od < opp_best:
                opp_best = od

        # Also encourage moving closer to at least one resource
        cur_mind = min(man(sx, sy, rx, ry) for rx, ry in top)
        new_mind = min(man(nx, ny, rx, ry) for rx, ry in top)

        # Score: minimize our distance; maximize opponent distance; reward improvement
        val = capture_bonus + (cur_mind - new_mind) * 5 + (opp_best - my_best) * 2 - new_mind
        if val > best_val:
            best_val = val
            best = (nx - sx, ny - sy)

    dx, dy = best
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]