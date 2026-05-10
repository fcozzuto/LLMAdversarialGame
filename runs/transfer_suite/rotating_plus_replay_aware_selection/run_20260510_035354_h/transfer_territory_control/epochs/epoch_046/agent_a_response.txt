def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    unclaimed = observation.get("unclaimed_cells") or []
    uset = {(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2}
    opp_terr = observation.get("opponent_territory") or []
    opset = {(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2}

    obstacles = observation.get("obstacles") or []
    oset = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**18, [0, 0])

    # Slightly bias toward our start corner expansion; later, bias toward cutting opponent.
    to_corner = man(ax, ay, 0, 0) + man(ox, oy, 7, 7)
    aggressive = 1.0 if to_corner > 8 else 0.0

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in oset:
            continue

        base = 0
        d_opp = man(nx, ny, ox, oy)
        d_uself = man(nx, ny, ax, ay)

        # Unclaimed is primary.
        if (nx, ny) in uset:
            base += 8000
            base += 2000 // (man(nx, ny, ox, oy) + 2)  # keep pressure away from opponent
            base += 5 // (d_uself + 1)
        elif (nx, ny) in opset:
            # Capturing opponent territory (flipping) can be valuable, especially if it reduces distance.
            base += 2200 + int(aggressive * 1200)
            base += 300 // (d_opp + 1)
            base -= 450 * man(nx, ny, ox, oy) // 10

        # Prefer moves that move toward nearest unclaimed if available nearby.
        if uset:
            # Consider only local few unclaimed points by simple deterministic scan near the move.
            local_best = 10**9
            for ux, uy in uset:
                md = man(nx, ny, ux, uy)
                if md < local_best:
                    local_best = md
            if local_best < 10**9:
                base += 350 // (local_best + 1)

        # Avoid dithering near opponent when not claiming.
        if (nx, ny) not in uset and (nx, ny) not in opset:
            base -= 80 * d_opp // 3

        # Tie-break deterministically: prefer smallest |dx| then |dy| then lexicographic.
        key = (base, -abs(dx), -abs(dy), -dx, -dy)
        if key > (best[0], -abs(best[1][0]), -abs(best[1][1]), -best[1][0], -best[1][1]):
            best = (base, [dx, dy])

    return [int(best[1][0]), int(best[1][1])]