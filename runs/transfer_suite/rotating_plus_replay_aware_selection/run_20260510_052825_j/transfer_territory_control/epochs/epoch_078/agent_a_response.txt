def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation.get("self_position", (0, 0))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    opp_pos = observation.get("opponent_position", None)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def edge_dist(cx, cy):
        return min(cx, w - 1 - cx, cy, h - 1 - cy)

    def step_score(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return -10**9
        gain = 0
        if (nx, ny) in unclaimed:
            gain += 6
        if (nx, ny) in oppT:
            gain += 4
        if (nx, ny) in selfT:
            gain += 1
        # Prefer perimeter expansion (opponent tends to center-claim)
        gain += (h + w - 2 * edge_dist(nx, ny)) * 0.05
        # Prefer moving toward our chosen frontier target implicitly (closer is better)
        if opp_pos and len(opp_pos) == 2:
            gain += 0.02 * (abs(nx - opp_pos[0]) + abs(ny - opp_pos[1]))
        return gain - 0.01 * (abs(nx - x) + abs(ny - y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort()  # deterministic tie-break
    best = (-(10**18), 0, 0)
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        s = step_score(nx, ny)
        if s > best[0]:
            best = (s, dx, dy)
    return [int(best[1]), int(best[2])]