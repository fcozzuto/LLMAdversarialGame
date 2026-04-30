def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # New strategy: one-step greedy on "who gets the next resource". If opponent is closer to all,
    # we pivot to reduce their lead most (intercept by minimizing opponent-next minus self-next).
    best_move = (0, 0)
    best_val = None
    # Deterministic resource ordering for tie breaks
    resources_sorted = sorted(resources, key=lambda t: (t[0], t[1]))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Immediate grab
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) in resources:
            val = 10**6
        else:
            self_best = 10**9
            opp_best = 10**9
            # Choose the resource that best discriminates who can reach first
            for (rx, ry) in resources_sorted:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # We model "next advantage" by opponent lead; take worst-case for us (minimize it).
                # If we can make opponent slower relative to us, that's good.
                # Use a "min over resources of (do - ds)"? But that can be too optimistic; instead we track max lead.
                lead = do - ds
                # For us, "good" means smaller lead; opponent may take a different resource, so consider best for opponent:
                if lead < self_best:
                    self_best = lead
                if do < opp_best:
                    opp_best = do

            # Convert into scalar: primary minimize (opponent lead after our move), then prefer proximity for ourselves
            # and slightly prefer moves that are closer to some resource (to avoid stalling).
            # self_best is min over resources of (do - ds), so lower is better.
            # Also compute our nearest distance to any resource.
            our_near = 10**9
            for (rx, ry) in resources_sorted:
                ds = cheb(nx, ny, rx, ry)
                if ds < our_near:
                    our_near = ds
            val = (-self_best) * 1000 - our_near

        # Tie-breaking: deterministic by dx,dy ordering already not guaranteed, so add coord-based stable ordering
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]