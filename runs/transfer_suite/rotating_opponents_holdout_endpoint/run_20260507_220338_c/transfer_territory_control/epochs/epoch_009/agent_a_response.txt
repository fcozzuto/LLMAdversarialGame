def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not ok(sx, sy):
        return [0, 0]

    # Nearest relevant cells (small, deterministic sampling)
    un_list = list(unclaimed)
    opp_list = list(opp_terr)
    best_u = None
    best_u_d = 10**9
    for x, y in un_list[:32]:
        d = abs(x - sx) + abs(y - sy)
        if d < best_u_d:
            best_u_d = d
            best_u = (x, y)
    best_o = None
    best_o_d = 10**9
    for x, y in opp_list[:32]:
        d = abs(x - sx) + abs(y - sy)
        if d < best_o_d:
            best_o_d = d
            best_o = (x, y)

    # If opponent territory is visible, prioritize close flips; else chase unclaimed.
    prefer = "opp" if best_o is not None and (best_o_d <= best_u_d or best_u is None) else "un"

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Opponent position used only for mild spacing (keeps determinism)
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(ox), int(oy)

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
        cell = (nx, ny)

        val = 0
        if cell in opp_terr:
            val += 8
        elif cell in unclaimed:
            val += 4
        elif cell in self_terr:
            val += 1
        else:
            val += 0

        # Distance shaping toward chosen targets
        if prefer == "opp" and best_o is not None:
            val += max(0, 5 - (abs(nx - best_o[0]) + abs(ny - best_o[1])))
        elif prefer == "un" and best_u is not None:
            val += max(0, 5 - (abs(nx - best_u[0]) + abs(ny - best_u[1])))

        # Mild penalty if stepping away from opponent when we can flip; mild penalty for being too close
        d_from_opp = abs(nx - ox) + abs(ny - oy)
        if cell in opp_terr:
            val += 2 if d_from_opp <= abs(sx - ox) + abs(sy - oy) else 0
        val -= 0.05 * max(0, d_from_opp - 1)

        # Prefer moves that change position when values tie
        if dx != 0 or dy != 0:
            val += 0.01

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]