def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def parse_pos(r):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return int(r[0]), int(r[1])
        if isinstance(r, dict):
            pos = r.get("position", r.get("pos", None))
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                return int(pos[0]), int(pos[1])
        return None
    targets = []
    for r in resources:
        p = parse_pos(r)
        if p:
            x, y = p
            if inb(x, y) and (x, y) not in obs:
                targets.append((x, y))
    if not targets:
        return [0, 0]

    best = None
    # Meaningful change vs prior: prioritize resources where we have a lead (opp is farther),
    # otherwise still pick a resource with strongest projected advantage.
    for tx, ty in targets:
        sd = abs(tx - sx) + abs(ty - sy)
        od = abs(tx - ox) + abs(ty - oy)
        margin = od - sd  # positive means we are closer
        val = (margin, -sd)  # maximize margin, then minimize our distance
        if best is None or val > best[0]:
            best = (val, (tx, ty))
    _, (tx, ty) = best

    # Greedy step: among legal moves, pick one that increases lead to target,
    # with a small bonus for moving towards any target where we lead.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sd = abs(tx - nx) + abs(ty - ny)
        od = abs(tx - ox) + abs(ty - oy)
        lead = od - sd
        # bonus: if we can get closer to any leading target in this one step
        bonus = -10**9
        for px, py in targets:
            sdp = abs(px - nx) + abs(py - ny)
            odp = abs(px - ox) + abs(py - oy)
            m = odp - sdp
            if m > bonus:
                bonus = m
        score = (lead, bonus, -sd)
        cand.append((score, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort(reverse=True)
    return [int(cand[0][1]), int(cand[0][2])]