def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def neigh_count(nx, ny, S):
        c = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            ax, ay = nx + dx, ny + dy
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in S:
                c += 1
        return c

    # Targeting heuristic: steal opponent cells if possible; otherwise expand into unclaimed
    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue

        score = 0.0

        if (nx, ny) in oppT:
            score += 14.0  # direct flip pressure
        if (nx, ny) in selfT:
            score -= 0.5  # less value than expansion
        if (nx, ny) in unclaimed:
            score += 6.5  # claim new territory

        # Frontier quality
        score += 1.5 * neigh_count(nx, ny, selfT)
        score += 2.0 * neigh_count(nx, ny, unclaimed)

        # Threat: being adjacent to opponent tends to cause flips back
        score -= 1.8 * neigh_count(nx, ny, oppT)

        # If opponent is close overall, bias away from their territory
        if oppT:
            # compute min Manhattan distance from candidate to opponent territory (small and cheap)
            mind = 10**9
            for px, py in oppT:
                d = abs(nx - px) + abs(ny - py)
                if d < mind:
                    mind = d
                    if mind <= 1:
                        break
            score += 0.8 * mind  # farther is safer when expanding

        # Deterministic tie-break by direction preference order (dirs order already fixed)
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]