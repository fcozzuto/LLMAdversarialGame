def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # New tactic: target resources the opponent is closer to, and choose moves that shrink our distance
    # while increasing/maintaining opponent distance to that same target (interception-like).
    best_delta = (0, 0)
    best_val = None
    cur_best_target = None

    for rx, ry in resources:
        d_me = man(sx, sy, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        # prioritize "steal attempts": opponent closer, but we are not too far and path is reasonable
        steal = (d_opp - d_me) + (d_opp > d_me) * 3
        # tie-break toward closer-for-us
        steal -= 0.1 * d_me
        if best_val is None or steal > best_val:
            best_val = steal
            cur_best_target = (rx, ry)
    if cur_best_target is None:
        # fallback: go toward center, but also away from opponent a bit
        tx, ty = w // 2, h // 2
    else:
        tx, ty = cur_best_target

    base_opp = man(ox, oy, tx, ty)
    cur_me = man(sx, sy, tx, ty)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nm = man(nx, ny, tx, ty)
        no = base_opp  # opponent not moving now, but we measure relative progress
        # also consider secondary resource for a deterministic "next best" if target doesn't exist
        sec_penalty = 0
        for rx, ry in resources:
            if (rx, ry) != (tx, ty):
                sec_penalty += (man(nx, ny, rx, ry) - man(ox, oy, rx, ry) <= 0) * 0.05

        # maximize improvement (me getting closer), and prioritize not letting opponent keep clear line to many resources
        val = (cur_me - nm) * 3 - (no * 0) + (base_opp - nm) * 0.15 - sec_penalty
        # if already on target, stay (still allowed and terminal desirability)
        if (sx, sy) == (tx, ty):
            val += 10
        # deterministic tie-breaking: prefer diagonal then cardinal then stay
        if best_val is None or val > best_val or (val == best_val and (dx, dy) in [(1,1),(-1,1),(1,-1),(-1,-1),(0,1),(1,0),(-1,0),(0,-1),(0,0)] and (best_delta==(0,0) or (dx, dy)!=(0,0))):
            best_val = val
            best_delta = (dx, dy)

    return [int(best_delta[0]), int(best_delta[1])]