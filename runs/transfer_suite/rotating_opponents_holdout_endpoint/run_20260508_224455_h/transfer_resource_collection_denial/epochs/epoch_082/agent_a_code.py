def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources") or [])]
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    turns_remaining = int(observation.get("turns_remaining", 0))

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Prefer resources we can reach not later than opponent; if none, pick best net advantage.
    best = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        # win-likelihood heuristic: earlier/equal arrival dominates.
        arrive_bonus = 6000 if ds <= do else 0
        lead = (do - ds)  # positive if we are closer
        # mild time pressure: as time runs out, prioritize nearer resources.
        time_pen = (turns_remaining // 10) * ds
        score = arrive_bonus + lead * 1200 - ds * 8 - do * 2 - time_pen
        cand = (score, -lead, ds, rx, ry)
        if best is None or cand > best:
            best = cand

    _, _, _, tx, ty = best if best is not None else (0, 0, 0, sx, sy)

    # One-step move toward target, avoiding immediate obstacle when possible.
    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # minimize distance to target; break ties by keeping away from opponent (optional).
        d_to = manh(nx, ny, tx, ty)
        d_opp = manh(nx, ny, ox, oy)
        cand = (-(d_to), d_opp, -abs(dx) - abs(dy), dx, dy)
        if best_m is None or cand > best_m:
            best_m = cand

    if best_m is not None:
        return [int(best_m[3]), int(best_m[4])]

    # If all moves blocked, stay.
    return [0, 0]