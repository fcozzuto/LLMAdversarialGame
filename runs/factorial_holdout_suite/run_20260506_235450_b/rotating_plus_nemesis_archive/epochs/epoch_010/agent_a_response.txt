def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by):
        dx = ax - bx;  dy = ay - by
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    # If no info/resources, drift toward farthest corner from opponent (deterministic)
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: man(ox, oy, c[0], c[1]) - man(sx, sy, c[0], c[1]))
        best = None; bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: continue
            v = -man(nx, ny, tx, ty)
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best if best is not None else [0, 0]

    scores = observation.get("scores") or {}
    self_name = observation.get("self_name"); opp_name = observation.get("opponent_name")
    my_score = scores.get(self_name, 0.0); opp_score = scores.get(opp_name, 0.0)
    leading = my_score >= opp_score

    # Precompute min distances to each resource for both agents
    # Scoring aims to reach a resource where we are at least not worse,
    # and to deny resources where opponent would be closer.
    best_overall = [0, 0]; best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        adj_obs = 0
        for obx, oby in obstacles:
            if man(nx, ny, obx, oby) == 1:
                adj_obs += 1

        # Evaluate position w.r.t. resources
        # Choose the best "target advantage" resource for us, and apply penalty for
        # resources where opponent advantage is emerging.
        target_gain = -10**18
        deny_pen = 0.0
        nearest_any = 10**9

        for rx, ry in resources:
            d_my = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            nearest_any = min(nearest_any, d_my)

            # Advantage: we want d_op - d_my positive (we are closer than opponent)
            adv = d_op - d_my

            # Favor small d_my, especially when not leading we need faster pickups.
            speed = -d_my
            score_local = 3.0 * adv + 1.0 * speed

            # If opponent already closer (adv <= 0), still allow if we are nearly tied
            # and can reach quickly.
            if adv > 0:
                score_local += 2.0

            if score_local > target_gain:
                target_gain = score_local

            # Deny: if opponent is much closer and we move away, penalize.
            # Deny based on how likely opponent can reach sooner than we can after this move.
            if d_op + (0 if leading else -1) < d_my:
                deny_pen += (d_my - d_op) * 1.2

        # Additional behavior: when trailing, prioritize fastest reachable resource overall.
        # When leading, prioritize denying: reduce opponent reach by moving toward resources
        # they are not closest to.
        if leading:
            v = 1.5 * target_gain - 1.8 * deny_pen - 0.25 * adj_obs
        else:
            v = 2.2 * target_gain - 1.0 * deny_pen + 0.8 * (-nearest_any) - 0.3 * adj_obs

        # Tiny deterministic tie-break: prefer not to increase distance to nearest resource
        # based on current state (encourages movement when safe).
        v -= 0.01 * (man(nx, ny, sx, sy))

        if v > best_score:
            best_score = v
            best_overall = [dx, dy]

    return best_overall