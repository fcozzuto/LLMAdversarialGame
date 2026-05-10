def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sx), int(sy)
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles

    unclaimed = observation.get("unclaimed_cells", []) or []
    un_set = set()
    for p in unclaimed:
        try:
            x, y = int(p[0]), int(p[1])
        except Exception:
            continue
        if inb(x, y) and not blocked(x, y):
            un_set.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_pos = observation.get("opponent_position", None)
    if isinstance(opp_pos, (list, tuple)) and len(opp_pos) >= 2:
        ox, oy = int(opp_pos[0]), int(opp_pos[1])
    else:
        ox, oy = None, None

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if blocked(sx, sy):
        return [0, 0]

    best_move = [0, 0]
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        sc = 0
        if (nx, ny) in un_set:
            sc += 200
        if (nx, ny) in self_terr:
            sc += 20
        if ox is not None:
            d = abs(nx - ox) + abs(ny - oy)
            sc += -d
        if un_set:
            dmin = min(abs(tx - nx) + abs(ty - ny) for (tx, ty) in un_set)
            sc += -dmin // 2
        if sc > best_sc or (sc == best_sc and (dx, dy) < (best_move[0], best_move[1])):
            best_sc = sc
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]