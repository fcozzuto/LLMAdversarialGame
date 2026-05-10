def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in (observation.get("obstacles") or []))
    self_terr = set((x, y) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((x, y) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((x, y) for x, y in (observation.get("unclaimed_cells") or []))

    if not unclaimed:
        targets = list(opp_terr) if opp_terr else list(self_terr)
        if not targets:
            return [0, 0]
        tx, ty = min(targets, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-(10**9), 0, 0)

    unclaimed_list = list(unclaimed)
    opp_pos = (ox, oy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        man_to_opp = abs(nx - ox) + abs(ny - oy)
        if (nx, ny) in self_terr:
            cell_bonus = 1.0
        elif (nx, ny) in unclaimed:
            cell_bonus = 3.0
        elif (nx, ny) in opp_terr:
            cell_bonus = 4.0
        else:
            cell_bonus = 0.5

        d_un = min(abs(nx - ux) + abs(ny - uy) for ux, uy in unclaimed_list)
        score = cell_bonus * 10.0 + (8.0 - d_un) + (2.0 - 0.05 * man_to_opp)

        # Tie-break deterministically toward moves that increase Manhattan distance from opponent (defensive expansion)
        far_from_opp = man_to_opp
        if score > best[0] or (score == best[0] and (far_from_opp > best[1] or (far_from_opp == best[1] and (dx, dy) < (best[2], best[0])))):
            best = (score, far_from_opp, dx)
            best = (score, far_from_opp, dx, dy)

    return [best[2], best[3]] if isinstance(best, tuple) and len(best) == 4 else [0, 0]