def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < W and 0 <= by < H:
                blocked.add((bx, by))

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    opp_set = set((int(x), int(y)) for x, y in opp_terr if x is not None and y is not None)

    unclaimed = observation.get("unclaimed_cells") or []
    un_set = set((int(x), int(y)) for x, y in unclaimed if x is not None and y is not None)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in blocked

    # Immediate counterclaim if possible
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny) and (nx, ny) in opp_set:
            return [dx, dy]

    # Otherwise, head to best unclaimed cell (or stay if none)
    if not un_set:
        return [0, 0]

    # Deterministic tie-break via a fixed scan order: prefer closer cells by squared distance,
    # then prefer cells closer to center to avoid getting cornered.
    cx, cy = (W - 1) // 2, (H - 1) // 2
    best_target = None
    best_key = None
    for (tx, ty) in un_set:
        dd = (tx - sx) * (tx - sx) + (ty - sy) * (ty - sy)
        dc = (tx - cx) * (tx - cx) + (ty - cy) * (ty - cy)
        key = (dd, dc, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (tx, ty)

    tx, ty = best_target
    # Greedy step toward target among valid moves
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Prefer reducing distance; slight preference for moving into unclaimed.
        val = ((tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)) * 100
        if (nx, ny) in un_set:
            val -= 1
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]
    return best_move