def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            # Engine will keep us in place if invalid; we heavily penalize obstacle "moves"
            candidates.append(((-10**9), dx, dy))
            continue

        # Immediate objective: steal/flip opponent territory if possible.
        if (nx, ny) in opp_terr:
            base = 500.0
        elif (nx, ny) in unclaimed:
            base = 80.0
        elif (nx, ny) in self_terr:
            base = 5.0
        else:
            base = 10.0

        # Distance shaping: prefer closer to opponent territory; avoid going away.
        if opp_terr:
            dmin = min(abs(nx - tx) + abs(ny - ty) for (tx, ty) in opp_terr)
            ds = abs(nx - ox) + abs(ny - oy)
            base += (120 - 2.0 * dmin)
            base += (-0.5 * ds)  # modestly discourage moving deeper toward opponent position
        else:
            # If no opponent territory known, expand toward nearest unclaimed.
            if unclaimed:
                dmin = min(abs(nx - tx) + abs(ny - ty) for (tx, ty) in unclaimed)
                base += (60 - 1.2 * dmin)

        # Micro-avoid: discourage stepping into cells adjacent to obstacles too much.
        adj_obs = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                px, py = nx + ex, ny + ey
                if (px, py) in obstacles:
                    adj_obs += 1
        base -= 3.0 * adj_obs

        # Tie-break deterministically by dx,dy order already fixed by moves list.
        candidates.append((base, dx, dy))

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]