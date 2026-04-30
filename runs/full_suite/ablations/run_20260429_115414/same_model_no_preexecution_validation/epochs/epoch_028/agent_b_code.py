def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]) or [0, 0])
    ox, oy = map(int, observation.get("opponent_position", [0, 0]) or [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid_res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                valid_res.append((x, y))

    dirs = [(-1, -1),(0, -1),(1, -1),(-1, 0),(0, 0),(1, 0),(-1, 1),(0, 1),(1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # Target scoring: prefer closer to us, far from opponent; tie-break toward nearer overall
    def target_value(tx, ty, extra_avoid):
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # small deterministic obstacle avoidance to reduce getting stuck: discourage targeting very "blocked" cells
        block_cnt = 0
        for dx, dy in dirs:
            nx, ny = tx + dx, ty + dy
            if inb(nx, ny) and (nx, ny) in obs:
                block_cnt += 1
        return (do - ds) - 0.15 * block_cnt + extra_avoid

    # If no resources, drift toward opponent side's corner deterministically (down-right relative to us)
    if not valid_res:
        tx, ty = (w - 1, h - 1) if (sx + sy) < (ox + oy) else (0, 0)
        best_target = (tx, ty)
    else:
        best_target = valid_res[0]
        best_tv = -10**18
        # Consider up to first few resources for speed/determinism, but deterministic order assumed from observation
        for i, (tx, ty) in enumerate(valid_res[:12]):
            tv = target_value(tx, ty, 0.0)
            if tv > best_tv:
                best_tv = tv
                best_target = (tx, ty)

    tx, ty = best_target

    # Evaluate candidate moves
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Primary: decrease distance to chosen target
        dist_to_target_before = cheb(sx, sy, tx, ty)
        dist_to_target_after = cheb(nx, ny, tx, ty)
        gain = dist_to_target_before - dist_to_target_after

        # Secondary: avoid moving into regions adjacent to obstacles (local stability)
        adj_obs = 0
        for ddx, ddy in dirs:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay) and (ax, ay) in obs:
                adj_obs += 1

        # Tertiary: don't let opponent get too close; prefer positions that keep their cheb-distance larger
        opp_dist = cheb(ox, oy, nx, ny)

        # Blend: winning pressure toward target, then safety/denial
        score = 10.0 * gain + 0.05 * opp_dist - 0.2 * adj_obs

        # Additional pressure: if move also improves our overall best resource heuristic, boost slightly
        if valid_res:
            best_local = -10**18
            # check a few nearest candidates deterministically
            for rx, ry in valid_res[:6]:
                ds_after = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                val = (do - ds_after) - 0.05 * (cheb(rx, ry, tx, ty))
                if val > best_local:
                    best_local = val
            score += 0.02 * best_local

        if score