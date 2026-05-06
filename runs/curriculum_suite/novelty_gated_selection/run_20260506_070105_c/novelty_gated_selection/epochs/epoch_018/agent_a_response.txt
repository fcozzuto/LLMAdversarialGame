def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    parity = observation.get("turn_index", 0) & 1

    best_dx, best_dy = 0, 0
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Deny/control: try to move toward resources where the opponent is currently closer,
        # while still keeping ourselves closer to some resource overall.
        total = 0
        for rx, ry in resources:
            my_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            gap = my_d - opp_d  # negative is good for us

            # Focus on contested / opponent-favored resources.
            contested = 1 if opp_d <= my_d else 0
            # If we are behind, emphasize denying by increasing opponent distance.
            deny = (opp_d - my_d) if my_d > opp_d else 0

            # Core score: want negative gap (we closer). Deny term when opponent-favored.
            score = (-gap) * (4 if contested else 2) + deny * 1.5
            # Slight preference for moving closer to the single best resource for us.
            total += score

        # Small deterministic tie-break: alternate preference directions by parity.
        tie = (dx + dy)
        if parity == 0:
            tie = -tie
        total += tie * 0.01

        if total > best_score:
            best_score = total
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]