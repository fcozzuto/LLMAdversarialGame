def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    unclaimed = observation.get("unclaimed_cells", []) or []
    self_terr = observation.get("self_territory", []) or []
    opp_terr = observation.get("opponent_territory", []) or []
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    self_set = set(map(tuple, self_terr))
    opp_set = set(map(tuple, opp_terr))

    best_target = None
    if unclaimed:
        best_key = None
        for tx, ty in unclaimed:
            if not cell_ok(tx, ty):
                continue
            ds = abs(tx - sx) + abs(ty - sy)
            do = abs(tx - ox) + abs(ty - oy)
            # Prefer targets closer to us, towards center, and where we are not far behind.
            key = (ds, abs(tx - cx) + abs(ty - cy), do)
            if best_key is None or key < best_key:
                best_key = key
                best_target = (tx, ty)
    if best_target is None:
        # If nothing unclaimed, attack: aim for opponent-owned cells adjacent to ours if possible.
        best_key = None
        for tx, ty in opp_terr:
            if not inb(tx, ty) or (tx, ty) in obstacles:
                continue
            neigh_self = False
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    if (tx + dx, ty + dy) in self_set:
                        neigh_self = True
                        break
                if neigh_self:
                    break
            ds = abs(tx - sx) + abs(ty - sy)
            do = abs(tx - ox) + abs(ty - oy)
            # Strongly prefer adjacent-to-ours to expand control.
            key = (0 if neigh_self else 1, ds, -do, abs(tx - cx) + abs(ty - cy))
            if best_key is None or key < best_key:
                best_key = key
                best_target = (tx, ty)

    tx, ty = best_target if best_target is not None else (sx, sy)

    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not cell_ok(nx, ny):
                continue
            # Favor moving towards target; also prefer stepping into opponent territory (flip) if it helps.
            dist = abs(tx - nx) + abs(ty - ny)
            flip_bonus = -2 if (nx, ny) in opp_set else 0
            avoid_opp_push = 0
            if (nx, ny) in opp_set:
                # discourage if opponent is already adjacent (likely to counter)
                if abs(nx - ox) + abs(ny - oy) <= 1:
                    avoid_opp_push = 1
            # Tie-break deterministically.
            score = (dist, avoid_opp_push + flip_bonus, abs(nx - cx) + abs(ny - cy), dx, dy)
            moves.append((score, [dx, dy]))
    moves.sort(key=lambda x: x[0])
    return moves[0][1] if moves else [0, 0]