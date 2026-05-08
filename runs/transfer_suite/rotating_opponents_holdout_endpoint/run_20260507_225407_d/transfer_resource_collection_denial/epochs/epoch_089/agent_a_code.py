def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    rem = observation.get("remaining_resource_count", None)
    rem = int(rem) if rem is not None else len(resources)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    alpha = 1.0 if rem <= 6 else 0.65  # later: more focus on deny

    def dist_manh(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # One-step lookahead: pick move maximizing expected collection advantage.
    best_score = -10**18
    best_move = (0, 0)

    # Deterministic tie-break: prefer moves closer to opponent-advantage direction? Keep fixed order.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine would keep us; replicate deterministically

        score = 0.0
        self_pos = (nx, ny)
        opp_pos = (ox, oy)

        for r in resources:
            sd = dist_manh(self_pos, r)
            od = dist_manh(opp_pos, r)

            # Prefer immediate collection strongly.
            if sd == 0:
                score += 10.0
            elif sd == 1:
                score += 3.0
            else:
                score += 1.0 / (sd + 0.5)

            # Denial pressure: only matters when competition is close.
            # If we arrive sooner, score; if later, penalize.
            diff = od - sd
            if abs(diff) <= 3:
                score += alpha * diff
            else:
                score += 0.2 * diff

        # Small bias: keep moving toward the best current resource, not diagonals always.
        # (deterministic and cheap)
        anchor = resources[0]
        best_anchor = None
        best_ad = 10**9
        for r in resources:
            d = dist_manh((sx, sy), r)
            if d < best_ad:
                best_ad = d
                best_anchor = r
        anchor = best_anchor
        anchor_dir = (0, 0)
        if anchor[0] != sx:
            anchor_dir = (1 if anchor[0] > sx else -1, anchor_dir[1])
        if anchor[1] != sy:
            anchor_dir = (anchor_dir[0], 1 if anchor[1] > sy else -1)
        if (dx, dy) == anchor_dir:
            score += 0.15

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]