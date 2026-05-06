def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    legal = []
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = (0, 0)
    best_val = -10**18

    # Choose a target resource where we are ahead; otherwise just go nearest.
    target = None
    if resources:
        lead_best = None
        lead_val = -10**18
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            lead = do - ds
            # Prefer being earlier, then closer.
            cand = (lead, -ds)
            if lead_best is None or cand > lead_best:
                lead_best = cand
                lead_val = lead
                target = (rx, ry)
        # If we're not really ahead, still allow nearest.
        if lead_val <= 0:
            target = min(resources, key=lambda r: man(sx, sy, r[0], r[1]))
    else:
        # No resources: drift toward center while keeping distance from opponent.
        target = ((w - 1) / 2.0, (h - 1) / 2.0)

    tx, ty = target
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Main objective: reduce distance to chosen target.
        d_t = man(nx, ny, tx, ty) if isinstance(tx, float) else man(nx, ny, tx, ty)

        # Small bias: if there are resources, prefer moves that reduce "contested" lead.
        contested_pen = 0
        if resources:
            best_lead_after = -10**9
            for rx, ry in resources:
                ds = man(nx, ny, rx, ry)
                do = man(ox, oy, rx, ry)
                lead = do - ds
                if lead > best_lead_after:
                    best_lead_after = lead
            # Higher best lead is better; turn into penalty for low/negative lead.
            contested_pen = -best_lead_after

        # Repel from opponent to avoid being blocked/collisions.
        d_o = man(nx, ny, ox, oy)
        repel = -d_o

        # Evaluate: prioritize target, then lead, then repulsion.
        val = (-d_t * 100) + (-contested_pen * 10) + repel
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]