def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    def inb(px, py):
        return 0 <= px < w and 0 <= py < h

    occ = set()
    for p in obstacles:
        if p and len(p) >= 2:
            occ.add((int(p[0]), int(p[1])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    if not resources:
        # If no resources, drift toward center while avoiding obstacles.
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in occ:
                val = (-(abs(nx - tx) + abs(ny - ty)), nx, ny)
                if best_val is None or val > best_val:
                    best_val = val
                    best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Evaluate each candidate move by potential "advantage" to claim the best next resource.
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        # If we can step onto a resource, prioritize that strongly.
        hit = (nx, ny) in set((int(r[0]), int(r[1])) for r in resources)

        best_for_move = None
        # Deterministic tie-breaking by (resource_x, resource_y).
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; also avoid equal/behind.
            # Larger advantage is better; smaller absolute distances as secondary.
            advantage = (do - ds)  # positive means we reach earlier/tie better
            val = (advantage, -(ds + do), -ds, rx, ry)
            if best_for_move is None or val > best_for_move:
                best_for_move = val

        # Combine hit preference with move-level resource evaluation.
        move_val = (1 if hit else 0, best_for_move[0], best_for_move[1], best_for_move[2], nx, ny)
        if best_val is None or move_val > best_val:
            best_val = move_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]