def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    self_name = observation["self_name"]
    opp_name = observation["opponent_name"]
    scores = observation.get("scores") or {}
    self_score = scores.get(self_name, 0.0) if isinstance(scores, dict) else 0.0
    opp_score = scores.get(opp_name, 0.0) if isinstance(scores, dict) else 0.0
    need_recover = (observation.get("self_territory_count", 0) < observation.get("opponent_territory_count", 0)) or (self_score < opp_score)

    targets = opp_terr if need_recover else unclaimed
    if not targets:
        targets = (unclaimed if unclaimed else opp_terr)
    if not targets:
        targets = self_terr if self_terr else {(sx, sy)}

    # pick up to 20 closest targets deterministically by distance then coords
    best_t = None
    best_td = 10**9
    for tx, ty in targets:
        d = abs(tx - sx) + abs(ty - sy)
        if d < best_td or (d == best_td and (ty, tx) < (best_t[1], best_t[0]) if best_t else True):
            best_td = d
            best_t = (tx, ty)

    # prefer movement that enters unclaimed/opp territory; tie-break toward best target
    bx, by = best_t
    idx = int(observation.get("turn_index", 0)) % len(dirs)
    dirs = dirs[idx:] + dirs[:idx]
    cand_best = (0, 0, -10**9)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 6
        elif (nx, ny) in opp_terr:
            score += 10 if need_recover else 7
        elif (nx, ny) in self_terr:
            score += 2
        else:
            score += 1
        # approach best target
        nd = abs(bx - nx) + abs(by - ny)
        score += 3 - nd
        # keep away from obstacles a bit
        if (nx + dx, ny + dy) in obstacles:
            score -= 1
        if score > cand_best[2]:
            cand_best = (dx, dy, score)

    dx, dy, _ = cand_best
    if dx == 0 and dy == 0:
        # if all candidate moves were blocked, stay
        return [0, 0]
    return [int(dx), int(dy)]