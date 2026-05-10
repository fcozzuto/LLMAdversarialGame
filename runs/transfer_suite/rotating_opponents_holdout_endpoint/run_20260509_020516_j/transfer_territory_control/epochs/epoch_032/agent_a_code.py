def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (W - 1, H - 1))
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))
        except Exception:
            pass

    self_cells = set()
    for p in observation.get("self_territory") or []:
        try:
            self_cells.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    opp_cells = set()
    for p in observation.get("opponent_territory") or []:
        try:
            opp_cells.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        try:
            unclaimed.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obstacles:
            continue

        d_opp = abs(nx - ox) + abs(ny - oy)
        d_ctr = abs(nx - cx) + abs(ny - cy)

        if (nx, ny) in opp_cells:
            cell_val = 7.0
        elif (nx, ny) in self_cells:
            cell_val = 2.0
        elif (nx, ny) in unclaimed:
            cell_val = 4.5
        else:
            cell_val = 1.0

        # Prefer attacking if safe, otherwise claim toward center.
        val = cell_val + 0.9 * (7 - d_opp) - 0.03 * d_ctr - 0.01 * (dx * dx + dy * dy)

        # Small obstacle-awareness: don't move into a tight dead-end.
        neigh_blocked = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if 0 <= tx < W and 0 <= ty < H and (tx, ty) in obstacles:
                neigh_blocked += 1
        val -= 0.2 * neigh_blocked

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]