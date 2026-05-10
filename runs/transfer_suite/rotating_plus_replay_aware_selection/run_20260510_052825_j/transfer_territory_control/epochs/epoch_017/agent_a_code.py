def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    opp_pos = observation["opponent_position"]
    ox, oy = opp_pos if isinstance(opp_pos, (list, tuple)) and len(opp_pos) == 2 else (7, 7)

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    candidates = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        cell = (nx, ny)
        score = 0
        if cell in unclaimed:
            score += 7
        if cell in oppT:
            score += 10
        if cell in selfT:
            score += 2

        nearest_un_d = 10**9
        if unclaimed:
            for ux, uy in unclaimed:
                d = abs(ux - nx) + abs(uy - ny)
                if d < nearest_un_d:
                    nearest_un_d = d
            score += -0.7 * nearest_un_d

            nearest_opp_adj = 10**9
            # Encourage approaching frontier that is closer to opponent than to us to pre-empt sweepers
            for ux, uy in unclaimed:
                du = abs(ux - nx) + abs(uy - ny)
                do = abs(ux - ox) + abs(uy - oy)
                if do + 2 < du:
                    # Potentially "steal" contested space
                    if du < nearest_opp_adj:
                        nearest_opp_adj = du
            if nearest_opp_adj < 10**9:
                score += 2.0 - 0.3 * nearest_opp_adj

        else:
            nearest_opp_d = 10**9
            for tx, ty in oppT:
                d = abs(tx - nx) + abs(ty - ny)
                if d < nearest_opp_d:
                    nearest_opp_d = d
            if nearest_opp_d < 10**9:
                score += 1.5 - 0.6 * nearest_opp_d

        # If our territory exists, slightly prefer not to drift away from it
        if selfT:
            mind = 10**9
            for tx, ty in selfT:
                d = abs(tx - nx) + abs(ty - ny)
                if d < mind:
                    mind = d
            score += -0.15 * mind

        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]