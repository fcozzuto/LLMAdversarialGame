def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    rem = int(observation.get("remaining_resource_count", 0) or 0)
    endgame = rem <= 4

    # Evaluate by win-chance over all resources: (opp_distance - our_distance) to a targeted resource,
    # plus a tie-breaker that reduces opponent's potential next-step approach.
    best_move = None
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Prefer staying near line of resources late; otherwise focus on competitive capture.
        val = 0
        for rx, ry in resources:
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # Advantage: positive if we're closer than opponent.
            adv = opp_d - our_d
            # Stronger weight for endgame and closer targets.
            score = adv * (10 if endgame else 6) - our_d
            # Threat estimate: how well opponent can reduce its distance next.
            # Since opponent policy is unknown, approximate by best single step toward target.
            opp_best = 10**9
            for odx, ody in dirs:
                tx, ty = ox + odx, oy + ody
                if inb(tx, ty) and (tx, ty) not in obstacles:
                    d = man(tx, ty, rx, ry)
                    if d < opp_best:
                        opp_best = d
            score -= (man(ox, oy, rx, ry) - opp_best)  # discourage giving opponent a big immediate improvement
            if score > val:
                val = score
        # If no resources, head toward center while avoiding obstacles.
        if not resources:
            cx, cy = (W - 1) // 2, (H - 1) // 2
            val = -man(nx, ny, cx, cy)
        # Deterministic tie-break: prefer moves with smallest dx, then dy, then lexicographic on position.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            cand = (dx, dy, nx, ny)
            cur = (best_move[0], best_move[1], sx + best_move[0], sy + best_move[1])
            if cand < cur:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]