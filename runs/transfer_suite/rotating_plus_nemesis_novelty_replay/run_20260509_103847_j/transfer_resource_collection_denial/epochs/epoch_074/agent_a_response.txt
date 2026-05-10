def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        # Prefer resources we can reach sooner; if both can, prefer the bigger gap; tie by nearer and coords
        key = (-(ds - do), -do, ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        ns = abs(tx - nx) + abs(ty - ny)
        # Small secondary pressure: prevent letting opponent gain while we move
        opp_gain = (abs(tx - ox) + abs(ty - oy)) - (abs(tx - ox) + abs(ty - oy))  # 0 but keeps structure deterministic
        key = (ns, abs(dx) + abs(dy), opp_gain, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, (dx, dy))
    return [best_move[1][0], best_move[1][1]]