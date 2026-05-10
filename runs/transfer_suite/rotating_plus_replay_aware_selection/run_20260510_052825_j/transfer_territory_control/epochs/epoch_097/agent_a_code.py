def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    opp_pos = observation.get("opponent_position", None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    nbr_dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    cand = []
    un_list = list(unclaimed) if unclaimed else []
    opp_pos = tuple(opp_pos) if isinstance(opp_pos, (list, tuple)) and len(opp_pos) == 2 else None

    def nearest_unclaimed_dist(x, y):
        if not un_list:
            return 0
        best = 10**9
        for ux, uy in un_list:
            d = abs(ux - x) + abs(uy - y)
            if d < best:
                best = d
        return best

    for dx, dy in nbr_dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            cand.append(((-10**9), dx, dy))
            continue
        if (nx, ny) in obstacles:
            cand.append(((-10**9), dx, dy))
            continue

        score = 0.0
        if (nx, ny) in unclaimed:
            score += 10.0
        if (nx, ny) in oppT:
            score += 8.0  # likely flips on entry
        if (nx, ny) in selfT:
            score += 2.0

        # Threat/pressure: avoid stepping into areas adjacent to many opponent cells
        threat = 0
        for adx, ady in nbr_dirs:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay) and (ax, ay) in oppT:
                threat += 1
        score -= 0.6 * threat

        # Advance toward unclaimed territory unless we're about to contest opponent cells
        if (nx, ny) not in oppT:
            score -= 0.25 * nearest_unclaimed_dist(nx, ny)

        # Slightly prefer moving away from opponent position if known
        if opp_pos is not None:
            od = abs(opp_pos[0] - nx) + abs(opp_pos[1] - ny)
            score += 0.02 * od

        cand.append((score, dx, dy))

    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, best_dx, best_dy = cand[0]
    return [int(best_dx), int(best_dy)]