def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w, h = observation.get("grid_width", 1), observation.get("grid_height", 1)
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}
    unclaimed = observation.get("unclaimed_cells") or []
    un = {(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2}
    resources = observation.get("resources") or []
    res = [(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2]
    opp = observation.get("opponent_position", None)

    myc = observation.get("scores", {}).get("self", None)
    opc = observation.get("scores", {}).get("opponent", None)
    if myc is None: myc = observation.get("self_territory_count", 0)
    if opc is None: opc = observation.get("opponent_territory_count", 0)
    behind = myc <= opc

    tx, ty = None, None
    if behind and opp is not None:
        tx, ty = opp[0], opp[1]
    else:
        if res:
            best = None
            bd = 10**18
            for x, y in res:
                d = max(abs(x - sx), abs(y - sy))
                if d < bd:
                    bd, best = d, (x, y)
            tx, ty = best
        elif un:
            best = None
            bd = 10**18
            for x, y in un:
                d = max(abs(x - sx), abs(y - sy))
                if d < bd:
                    bd, best = d, (x, y)
            tx, ty = best
        elif opp is not None:
            tx, ty = opp[0], opp[1]
        else:
            tx, ty = sx, sy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move, best_val = (0, 0), -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        val = -max(abs(tx - nx), abs(ty - ny))
        if (nx, ny) in un:
            val += 2
        if (nx, ny) in obs:
            val -= 100
        if val > best_val:
            best_val, best_move = val, [dx, dy]

    return best_move